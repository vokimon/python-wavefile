try:
    from enum import IntFlag
except ImportError: # pragma: no cover
    from enum import Enum, IntEnum

    class IntFlag(IntEnum):
        def __or__(self, other):
            return self.__class__(self._value_ | self.__class__(other)._value_)
        def __and__(self, other):
            return self.__class__(self._value_ & self.__class__(other)._value_)

        @classmethod
        def _missing_(cls, value):
            """
            Returns member (possibly creating it) if one can be found for value.
            """
            if not isinstance(value, int):
                raise ValueError("%r is not a valid %s" % (value, cls.__qualname__))
            new_member = cls._create_pseudo_member_(value)
            return new_member

        @classmethod
        def _create_pseudo_member_(cls, value):
            """
            Create a composite member iff value contains only members.
            """
            pseudo_member = cls._value2member_map_.get(value, None)
            if pseudo_member is None:
                need_to_create = [value]
                # get unaccounted for bits
                _, extra_flags = _decompose(cls, value)
                # timer = 10
                while extra_flags:
                    # timer -= 1
                    bit = _high_bit(extra_flags)
                    flag_value = 2 ** bit
                    if (flag_value not in cls._value2member_map_ and
                            flag_value not in need_to_create
                            ):
                        need_to_create.append(flag_value)
                    if extra_flags == -flag_value:
                        extra_flags = 0
                    else:
                        extra_flags ^= flag_value
                for value in reversed(need_to_create):
                    # construct singleton pseudo-members
                    pseudo_member = int.__new__(cls, value)
                    pseudo_member._name_ = None
                    pseudo_member._value_ = value
                    # use setdefault in case another thread already created a composite
                    # with this value
                    pseudo_member = cls._value2member_map_.setdefault(value, pseudo_member)
            return pseudo_member

    def _high_bit(value):
        """
        returns index of highest bit, or -1 if value is zero or negative
        """
        return value.bit_length() - 1

    def _decompose(flag, value):
        """
        Extract all members from the value.
        """
        # _decompose is only called if the value is not named
        not_covered = value
        negative = value < 0
        members = []
        for member in flag:
            member_value = member.value
            if member_value and member_value & value == member_value:
                members.append(member)
                not_covered &= ~member_value
        if not negative:
            tmp = not_covered
            while tmp:
                flag_value = 2 ** _high_bit(tmp)
                if flag_value in flag._value2member_map_:
                    members.append(flag._value2member_map_[flag_value])
                    not_covered &= ~flag_value
                tmp &= ~flag_value
        if not members and value in flag._value2member_map_:
            members.append(flag._value2member_map_[value])
        members.sort(key=lambda m: m._value_, reverse=True)
        if len(members) > 1 and members[0].value == value:
            # we have the breakdown, don't need the value member itself
            members.pop(0)
        return members, not_covered


