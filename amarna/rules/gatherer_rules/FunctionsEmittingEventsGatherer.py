from typing import List
from lark import Tree
from amarna.Result import PositionType, getPosition
from amarna.rules.GenericGatherer import GenericGatherer
from dataclasses import dataclass


@dataclass
class EventEmitType:
    """Represents an event emit (a function call of the emit method for a @event function)."""

    event_name: str
    event_emit_position: PositionType


@dataclass
class FunctionEmittingEvent:
    """A function that emits events, and their locations."""

    function_name: str
    function_position: PositionType
    function_location: str
    events_emitted_list: List[EventEmitType]


class FunctionsEmittingEventsGatherer(GenericGatherer):
    GATHERER_NAME = "FunctionsEmittingEvents"

    def __init__(self) -> None:
        super().__init__()
        self.functions_emitting_events: List[FunctionEmittingEvent] = []

    def get_gathered_data(self) -> List[FunctionEmittingEvent]:
        return self.functions_emitting_events

    def code_element_function(self, tree: Tree) -> None:
        function_name = None

        for child in tree.children:
            if child.data == "identifier_def":
                function_name = str(child.children[0])
                break

        assert function_name != None

        events_emitted_list: List[EventEmitType] = []

        for call in tree.find_data("function_call"):
            if len(call.children) > 0:
                ids = call.children[0]
                assert ids.data == "identifier"
                if len(ids.children) == 2 and ids.children[1] == "emit":
                    event_name = ids.children[0]
                    event_position = getPosition(ids)
                    events_emitted_list.append(EventEmitType(event_name, event_position))

        if events_emitted_list:
            event = FunctionEmittingEvent(
                function_name, getPosition(tree), self.fname, events_emitted_list
            )
            self.functions_emitting_events.append(event)
