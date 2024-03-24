

class SubGroupCreator:
    """this class groups a list of items into subgroups of specified number of items, with the last item
        being equal to or less than the specified number
    """
    def __init__(self, data):
        self.data = data
        self.sub_group_size = 0
        self.sub_groups = []

    def create_sub_groups(self, sub_group_size):
        self.sub_group_size = sub_group_size
        if sub_group_size <= 0:
            raise ValueError("Sub-group size should be greater than zero.")

        # Calculate the total number of subgroups
        num_sub_groups = -(-len(self.data) // sub_group_size)

        # Divide the data into subgroups
        start = 0
        for i in range(num_sub_groups):
            end = start + sub_group_size
            self.sub_groups.append(self.data[start:end])
            start = end

    def total_groups(self):
        return len(self.sub_groups)

    def get_group(self, group_number):
        if group_number < 1 or group_number > len(self.sub_groups):
            raise ValueError("Invalid group number.")
        return self.sub_groups[group_number - 1]