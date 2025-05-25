# def get_selected_data(data: str) -> int:
#     data_lst = data.split("_")
#     return int(data_lst[-1])
import json

class ButtonCallbackParams:
    def __init__(self, button_name, cat=None, subcat = None, page = 1):
        self.button_name = button_name
        self.cat = cat
        self.subcat = subcat
        self.page = page

    def to_json_string(self) -> str:
        return self.button_name + "_" + json.dumps({key:value for key, value in self.__dict__.items() if key!= "button_name"})

    @classmethod
    def from_callback(cls, data: str):
        data_lst = data.split("_")
        if len(data_lst) < 2:
            return None
        data = json.loads(data_lst[-1])
        return cls(
            button_name=data.get(data_lst[0]),
            cat=data.get("cat"),
            subcat=data.get("subcat"),
            page=data.get("page", 1)
        )
