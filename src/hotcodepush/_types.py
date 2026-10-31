class NotGiven:
    """The type of `NOT_GIVEN`, the default of every optional argument.

    An argument left at `NOT_GIVEN` stays out of the request. `None` sends JSON `null` where the
    API takes it, for example to clear a channel's `expires_at`.
    """

    def __repr__(self) -> str:
        return "NOT_GIVEN"


NOT_GIVEN = NotGiven()
