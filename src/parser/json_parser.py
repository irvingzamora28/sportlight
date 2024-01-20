class JSONParser:
    """
    A class to parse JSON data and extract values based on a specified path.
    """

    @staticmethod
    def find_value_in_list(data_list, key, value, target_keys):
        """
        Searches for a dictionary in a list where the given key has the specified value
        and then navigates through nested dictionaries based on target_keys to return the final value.

        Parameters:
            data_list (list): A list of dictionaries to search.
            key (str): The key to check the value against.
            value (str): The value to look for.
            target_keys (list): A list of keys representing the path to the desired value.

        Returns:
            The value found at the end of the target_keys path if found, otherwise None.
        """
        for item in data_list:
            if item.get(key) == value:
                return JSONParser.extract_value(item, target_keys)
        return None

    @staticmethod
    def extract_value(data, path):
        """
        Extracts a value from nested dictionaries given a specified path.

        Parameters:
            data (dict): The data dictionary to extract the value from.
            path (list): A list of keys representing the path to the desired value.

        Returns:
            The value if found, otherwise None.
        """
        for key in path:
            if isinstance(data, dict):
                data = data.get(key)
            else:
                return None
        return data
