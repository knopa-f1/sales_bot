def get_selected_data(data: str) -> str:
    data_lst = data.split("_")
    return data_lst[-1]

def get_selected_data_subcat(data: str) -> tuple:
    data_lst = data.split("_")
    return data_lst[-1], data_lst[len(data_lst)-2]