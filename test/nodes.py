from larvik.discover import register_node, NodeType


@register_node("testnode")
class ReflectionShow(NodeType):
    type = "admin"
    settings = {"reload": True}
    name = "Test"
    path = "TestingAdmi"
