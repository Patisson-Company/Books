from collections.abc import Iterable
from typing import Any, Optional, Self

from sqlalchemy import Column, Select


class Stmt:
    
    def __init__(self, stmt: Select) -> None:
        self.stmt = stmt
       
        
    def __call__(self) -> Select:
        return self.stmt 
        
        
    def lte_filter(self, column: Column, op: Optional[Any]) -> Self:
        '<='
        if op: self.stmt = self.stmt.filter(column <= op) if op else self.stmt
        return self
        
        
    def gte_filter(self, column: Column, op: Optional[Any]) -> Self:
        '>='
        if op: self.stmt = self.stmt.filter(column >= op) if op else self.stmt
        return self
        
        
    def lt_filter(self, column: Column, op: Optional[Any]) -> Self:
        '<'
        if op: self.stmt = self.stmt.filter(column < op) if op else self.stmt
        return self
      
      
    def lt_filter(self, column: Column, op: Optional[Any]) -> Self:
        '>'
        if op: self.stmt = self.stmt.filter(column > op) if op else self.stmt
        return self
        
        
    def eq_filter(self, column: Column, op: Optional[Any]) -> Self:
        '=='
        if op: self.stmt = self.stmt.filter(column == op)
        return self
       
       
    def con_filter(self, column: Column, ops: Optional[Iterable[Any]]) -> Self:
        'in'
        if ops: self.stmt = self.stmt.filter(column.in_(ops))
        return self
    
    
    def con_model_filter(self, column: Column, ops: Optional[Iterable[Any]]) -> Self:
        '"in" for relationship'
        if ops:
            self.stmt = self.stmt.filter(column.any(column.property.mapper.class_.name.in_(ops)))
        return self
    
    
    def limit(self, num: Optional[int]) -> Self:
        self.stmt = self.stmt.limit(num) if num else self.stmt
        return self    