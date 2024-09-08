from collections.abc import Iterable
from typing import Any, Optional, Self

from sqlalchemy import Column, Select
from sqlalchemy.orm import InstrumentedAttribute


class Stmt:
    
    def __init__(self, stmt: Select) -> None:
        self.stmt = stmt
       
        
    def __call__(self) -> Select:
        return self.stmt 
        
        
    def lte_filter(self, column: Column, op: Optional[Any]) -> Self:
        '<='
        if op: self.stmt = self.stmt.filter(column <= op)
        return self
        
        
    def gte_filter(self, column: Column, op: Optional[Any]) -> Self:
        '>='
        if op: self.stmt = self.stmt.filter(column >= op)
        return self
        
        
    def lt_filter(self, column: Column, op: Optional[Any]) -> Self:
        '<'
        if op: self.stmt = self.stmt.filter(column < op)
        return self
      
      
    def gt_filter(self, column: Column, op: Optional[Any]) -> Self:
        '>'
        if op: self.stmt = self.stmt.filter(column > op)
        return self
        
        
    def eq_filter(self, column: Column, op: Optional[Any]) -> Self:
        '=='
        if op: self.stmt = self.stmt.filter(column == op)
        return self
       
       
    def con_filter(self, column: Column, ops: Optional[Iterable[Any]]) -> Self:
        'in'
        if ops: self.stmt = self.stmt.filter(column.in_(ops))
        return self
    
    
    def con_model_filter(self, column: InstrumentedAttribute[Any], ops: Optional[Iterable[Any]]) -> Self:
        '"in" for relationship'
        if ops:
            self.stmt = self.stmt.filter(column.any(column.property.mapper.class_.name.in_(ops)))
        return self
    
    
    def like_filter(self, column: Column, op: Optional[Iterable[Any]]) -> Self:
        'LIKE'
        if op: self.stmt = self.stmt.filter(column.like(op))
        return self
    
    
    def ordered_by(self, column: Optional[Column]) -> Self:
        if column is not None:
            self.stmt = self.stmt.order_by(column) 
        return self
    
    
    def limit(self, num: Optional[int]) -> Self:
        if num: self.stmt = self.stmt.limit(num)
        return self    
    
    
    def offset(self, num: Optional[int]) -> Self:
        if num: self.stmt = self.stmt.offset(num) 
        return self
    