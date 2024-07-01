from typing import Generic, TypeVar, Union, List, get_args

T = TypeVar('T')

class MyAnnotation(Generic[T]):
    _generic_type = None

    def __init__(self, value: Union[T, List[T]]):
        self.value = value
        if MyAnnotation._generic_type is None:
            MyAnnotation._generic_type = get_args(self.__orig_class__)[0]

    @staticmethod
    def check():
        if MyAnnotation._generic_type:
            print(f"Generic type is: {MyAnnotation._generic_type}")
        else:
            print("Generic type has not been set.")

# Usage
annotation_instance = MyAnnotation[int](4)
MyAnnotation.check()  # Should print: Generic type is: <class 'int'>

