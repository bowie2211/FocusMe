Design Decisisions
==================

Desigen Decision 1
##################

Topic:
The Dialog for adding a task is within the QCustumListWidet class.
An Object of that class does not have access to the data_model.
Problem to be solved: How is the data model updated with the new taks data that comes
from a kanban lane.

Solution variants:
1) Global variable for data_model
2) Provide the data_model to the QCostumListWidget
3) Use a callback-funktion in MainWindow


Decision:
Decison for Variante 3