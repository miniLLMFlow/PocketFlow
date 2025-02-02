
# from pocketflow import *
from __init__ import *
import os

def call_llm(prompt):
    # Your API logic here
    return prompt

class LoadFile(Node):
    def __init__(self, name=None):
        super().__init__()
        # Use provided name or fall back to automatic lookup
        self.name = name or self.name
    def prep(self, shared):
        print(f" In : {self.__class__.__name__}")
        """Load file from disk"""
        filename = self.params["filename"]
        with open(filename, "r") as file:
            return file.read()

    def exec(self, prep_res):
        """Return file content"""
        return prep_res

    def post(self, shared, prep_res, exec_res):
        """Store file content in shared"""
        shared["file_content"] = exec_res
        return "default"


class GetOpinion(Node):
    def __init__(self, name=None):
        super().__init__()
        # Use provided name or fall back to automatic lookup
        self.name = name or self.name
            
    def prep(self, shared):
        print(f" In : {self.__class__.__name__}")
        print(f"My name is: {self.name} (instance of {self.__class__.__name__})")
        if self.flow:
            print(f"Flow name: {self.flow.name}")
            if self.flow.parent:
                print(f"Parent flow: {self.flow.parent.name}")
        """Get file content from shared"""
        if not shared.get("reworked_file_content"):
            return shared["file_content"]
        else:
            return "Original text :\n" + shared["file_content"] + "Revised version:\n" + shared["reworked_file_content"]

    def exec(self, prep_res):
        """Ask LLM for opinion on file content"""
        prompt = f"What's your opinion on this text: {prep_res}. Provide opinion on how to make it better."
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        """Store opinion in shared"""
        shared["opinion"] = exec_res
        return "default"

class GetValidation(Node):
    def __init__(self, name=None):
        super().__init__()
        # Use provided name or fall back to automatic lookup
        self.name = name or self.name
    def prep(self, shared):
        print(f" In : {self.__class__.__name__}")
        """Get file content from shared"""
        shared['discussion'] = shared["file_content"] + shared["opinion"] + "Final revised text : " + shared["reworked_file_content"]
        return

    def exec(self, prep_res):
        """Ask LLM for opinion on file content"""
        prompt = f"Validate that the final revised text is valid and reflects the changes proposed in opinion : {prep_res}. \nReply `IS VALID` if it is of `NOT VALID` if it needs some more work."
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        """Store rework count in shared"""
        if "IS VALID" in exec_res:
            return "default"
        else:
            return "invalid"


class ReworkFile(Node):
    def __init__(self, name=None):
        super().__init__()
        # Use provided name or fall back to automatic lookup
        self.name = name or self.name
    def prep(self, shared):
        print(f" In : {self.__class__.__name__}")
        """Get file content and opinion from shared"""
        return shared["file_content"], shared["opinion"]

    def exec(self, prep_res):
        """Ask LLM to rework file based on opinion"""
        file_content, opinion = prep_res
        prompt = f"Rework this text based on the opinion: {opinion}\n\nOriginal text: {file_content}"
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        """Store reworked file content in shared"""
        if "rework2_flow_min_count" in self.params:
            rework_count = self.params["rework2_flow_min_count"]
            shared["reworked_file_content"] = exec_res
            if not shared.get("reworked_file_content_count"):
                shared["reworked_file_content_count"] = 1
            elif shared.get("reworked_file_content_count"):
                shared["reworked_file_content_count"] += 1

            if shared["reworked_file_content_count"] < rework_count:
                print(f"Less than {self.params["rework2_flow_min_count"]} rework for rework2_flow, so going for pass #{shared["reworked_file_content_count"]}.")
                return "rework"
            else:
                return "default"
        else:
            shared["reworked_file_content"] = exec_res


class SaveFile(Node):
    def __init__(self, name=None):
        super().__init__()
        # Use provided name or fall back to automatic lookup
        self.name = name or self.name
    def prep(self, shared):
        print(f" In : {self.__class__.__name__}")
        """Get reworked file content and original filename from shared"""
        filename = self.params["filename"]
        if "reworked_file_content" in shared:
            return shared["reworked_file_content"], filename
        else:
            print("Error")

    def exec(self, prep_res):
        """Save reworked file content to new file"""
        reworked_file_content, filename = prep_res
        new_filename = f"{filename.split('.')[0]}_v2.{filename.split('.')[-1]}"
        with open(new_filename, "w") as file:
            file.write(reworked_file_content)
        return reworked_file_content

    def post(self, shared, prep_res, exec_res):
        filename = self.params["filename"]
        """Return success message"""
        print(f"Saved to {filename} the content : \n{exec_res}")


# # # Comment this from here
# # First flow
# Create nodes
load_Node = LoadFile(name="load_Node")
opinion_Node = GetOpinion(name="opinion_Node")
rework_Node = ReworkFile(name="rework_Node")
save_Node = SaveFile(name="save_Node")

# Connect nodes
load_Node >> opinion_Node >> rework_Node >> save_Node

# Create flow
rework_Flow = Flow(start=load_Node,name="rework_Flow")

# Set flow params
rework_Flow.set_params({"filename": "example.txt"})
# Run flow
shared = {}
rework_Flow.run(shared)
# # # To here for second workflow to work

# # Second flow
# Create nodes
load2_Node = LoadFile(name="load2_Node")
opinion2_Node = GetOpinion(name="opinion2_Node")
rework2_Node = ReworkFile(name="rework2_Node")
valid2_Node = GetValidation(name="valid2_Node")
save2_Node = SaveFile(name="save2_Node")

print(f" NAME is : {opinion2_Node.name}")

# Connect nodes
load2_Node >> opinion2_Node
opinion2_Node >> rework2_Node

rework2_Node - "default" >> valid2_Node
rework2_Node - "rework" >> opinion2_Node

# Get second opinion it if rework asked because in rework_flow2 and less than 2 rework
valid2_Node - "invalid" >> opinion2_Node
valid2_Node - "default" >> save2_Node

# Create flow with explicit name
rework2_Flow = Flow(start=load2_Node, name="rework2_Flow")
# rework2_Flow.name = "rework2_Flow"  # Set explicit name

# Set flow params
# This will not set params if class Flow was already initialized with other params ?
rework2_Flow.set_params({"filename": "example.txt", "rework2_flow_min_count" : 3})

# Run flow
shared2 = {}
rework2_Flow.run(shared2)

def build_mermaid(start):
    visited, lines = set(), ["graph LR"]
    
    def get_name(n):
        """Get the node's name for use in the diagram"""
        if isinstance(n, Flow):
            return n._get_name()
        return n._get_name().replace(' ', '_')  # Mermaid needs no spaces in node names
    
    def link(a, b):
        lines.append(f"    {get_name(a)} --> {get_name(b)}")
    def walk(node, parent=None):
        if node in visited:
            return parent and link(parent, node)
        visited.add(node)
        if isinstance(node, Flow):
            node.start and parent and link(parent, node)
            # Add flow name and class name to subgraph label
            flow_label = f"{node._get_name()}  ({type(node).__name__})"
            lines.append(f"\n    subgraph {get_name(node)}[\"{flow_label}\"]")
            node.start and walk(node.start)
            for nxt in node.successors.values():
                node.start and walk(nxt, node.start) or (parent and link(parent, nxt)) or walk(nxt)
            lines.append("    end\n")
        else:
            # Add both instance name and class name to node label
            node_label = f"{node._get_name()} ({type(node).__name__})"
            lines.append(f"    {get_name(node)}[\"{node_label}\"]")
            parent and link(parent, node)
            [walk(nxt, node) for nxt in node.successors.values()]
    walk(start)
    return "\n".join(lines)

print(build_mermaid(start=rework_Flow))

print(build_mermaid(start=rework2_Flow))
