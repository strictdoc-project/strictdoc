import re


class RSTFieldParser:
    pattern_array_split = re.compile(r'(?:-\s)')
    pattern_dict_split = re.compile(r'(?:,\s+)|\n')

    @staticmethod
    def parse_dict_array(dict_array_string):
        array_members_raw = RSTFieldParser.pattern_array_split.split(dict_array_string)
        array_members_raw = [x for x in array_members_raw if x and x != '\n']

        key_values = []
        for array_member_raw in array_members_raw:
            field_dict = {}

            kv_pair_strs = RSTFieldParser.pattern_dict_split.split(array_member_raw)
            kv_pair_strs = [x for x in kv_pair_strs if x and x != '\n']

            for kv_pair_str in kv_pair_strs:
                kv_pair = kv_pair_str.split('=')
                assert len(kv_pair) == 2
                field_dict[kv_pair[0].strip()] = kv_pair[1].strip()
            key_values.append(field_dict)

        return key_values
