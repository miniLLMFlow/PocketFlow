import asyncio, warnings, copy, time, sys

class BaseNode:
    def __init__(self):
        self.params, self.successors = {}, {}
        self.name = self.get_instance_name() or f"node_{hash(self)}"
        self.flow = None  # Will be set by Flow._propagate_flow
        self.parent = None  # Will be set by Flow._propagate_flow
        
    def get_instance_name(self):
        """Find the variable name this instance is assigned to, if any"""
        try:
            frame = sys._getframe(1)
            while frame:
                for scope in (frame.f_locals, frame.f_globals):
                    for key, value in scope.items():
                        if value is self and not key.startswith('_') and key != 'self':
                            return key
                frame = frame.f_back
        except (AttributeError, ValueError):
            pass
        return None
        
    def _get_name(self):
        """Return the instance name, either from name attribute or lookup"""
        return self.name or self.get_instance_name() or f"node_{hash(self)}"
    def set_params(self,params): self.params=params
    def add_successor(self,node,action="default"):
        if action in self.successors: warnings.warn(f"Overwriting successor for action '{action}'")
        self.successors[action]=node;return node
    def prep(self,shared): pass
    def exec(self,prep_res): pass
    def post(self,shared,prep_res,exec_res): pass
    def _exec(self,prep_res): return self.exec(prep_res)
    def _run(self,shared): p=self.prep(shared);e=self._exec(p);return self.post(shared,p,e)
    def run(self,shared):
        if self.successors: warnings.warn("Node won't run successors. Use Flow.")
        return self._run(shared)
    def __rshift__(self,other): return self.add_successor(other)
    def __sub__(self,action):
        if isinstance(action,str): return _ConditionalTransition(self,action)
        raise TypeError("Action must be a string")

class _ConditionalTransition:
    def __init__(self,src,action): self.src,self.action=src,action
    def __rshift__(self,tgt): return self.src.add_successor(tgt,self.action)

class Node(BaseNode):
    def __init__(self,max_retries=1,wait=0): super().__init__();self.max_retries,self.wait=max_retries,wait
    def exec_fallback(self,prep_res,exc): raise exc
    def _exec(self,prep_res):
        for self.cur_retry in range(self.max_retries):
            try: return self.exec(prep_res)
            except Exception as e:
                if self.cur_retry==self.max_retries-1: return self.exec_fallback(prep_res,e)
                if self.wait>0: time.sleep(self.wait)

class BatchNode(Node):
    def _exec(self,items): return [super(BatchNode,self)._exec(i) for i in items]

class Flow(BaseNode):
    def __init__(self, start, name=None):
        super().__init__()
        self.start = start
        self.name = name or self.get_instance_name() or f"flow_{hash(self)}"
        self._propagate_flow(self.start)

    def _propagate_flow(self, node, visited=None):
        """Set flow and parent references on all nodes in the flow"""
        if visited is None:
            visited = set()
            
        if node is None or id(node) in visited:
            return
            
        visited.add(id(node))
        node.flow = self
        node.parent = self.parent if hasattr(self, 'parent') else None
        
        for successor in node.successors.values():
            self._propagate_flow(successor, visited)
    def get_next_node(self,curr,action):
        nxt=curr.successors.get(action or "default")
        if not nxt and curr.successors: warnings.warn(f"Flow ends: '{action}' not found in {list(curr.successors)}")
        return nxt
    def _orch(self, shared, params=None):
        curr, p = copy.copy(self.start), (params or {**self.params})
        while curr:
            curr.set_params(p)
            c = curr._run(shared)
            curr = copy.copy(self.get_next_node(curr, c))
    def _run(self,shared): pr=self.prep(shared);self._orch(shared);return self.post(shared,pr,None)
    def exec(self,prep_res): raise RuntimeError("Flow can't exec.")

class BatchFlow(Flow):
    def _run(self, shared):
        pr = self.prep(shared) or []
        for bp in pr:
            self._orch(shared, {**self.params, **bp})
        return self.post(shared, pr, None)

class AsyncNode(Node):
    def prep(self,shared): raise RuntimeError("Use prep_async.")
    def exec(self,prep_res): raise RuntimeError("Use exec_async.")
    def post(self,shared,prep_res,exec_res): raise RuntimeError("Use post_async.")
    def exec_fallback(self,prep_res,exc): raise RuntimeError("Use exec_fallback_async.")
    def _run(self,shared): raise RuntimeError("Use run_async.")
    async def prep_async(self,shared): pass
    async def exec_async(self,prep_res): pass
    async def exec_fallback_async(self,prep_res,exc): raise exc
    async def post_async(self,shared,prep_res,exec_res): pass
    async def _exec(self,prep_res):
        for i in range(self.max_retries):
            try: return await self.exec_async(prep_res)
            except Exception as e:
                if i==self.max_retries-1: return await self.exec_fallback_async(prep_res,e)
                if self.wait>0: await asyncio.sleep(self.wait)
    async def run_async(self,shared):
        if self.successors: warnings.warn("Node won't run successors. Use AsyncFlow.")
        return await self._run_async(shared)
    async def _run_async(self,shared): p=await self.prep_async(shared);e=await self._exec(p);return await self.post_async(shared,p,e)

class AsyncBatchNode(AsyncNode,BatchNode):
    async def _exec(self,items): return [await super(AsyncBatchNode,self)._exec(i) for i in items]

class AsyncParallelBatchNode(AsyncNode,BatchNode):
    async def _exec(self,items): return await asyncio.gather(*(super(AsyncParallelBatchNode,self)._exec(i) for i in items))

class AsyncFlow(Flow,AsyncNode):
    async def _orch_async(self, shared, params=None):
        curr, p = copy.copy(self.start), (params or {**self.params})
        while curr:
            curr.set_params(p)
            if isinstance(curr, AsyncNode):
                c = await curr._run_async(shared)
            else:
                c = curr._run(shared)
            curr = copy.copy(self.get_next_node(curr, c))
    async def _run_async(self,shared): p=await self.prep_async(shared);await self._orch_async(shared);return await self.post_async(shared,p,None)

class AsyncBatchFlow(AsyncFlow,BatchFlow):
    async def _run_async(self, shared):
        pr = await self.prep_async(shared) or []
        for bp in pr:
            await self._orch_async(shared, {**self.params, **bp})
        return await self.post_async(shared, pr, None)

class AsyncParallelBatchFlow(AsyncFlow,BatchFlow):
    async def _run_async(self, shared):
        pr = await self.prep_async(shared) or []
        await asyncio.gather(*(self._orch_async(shared, {**self.params, **bp}) for bp in pr))
        return await self.post_async(shared, pr, None)
