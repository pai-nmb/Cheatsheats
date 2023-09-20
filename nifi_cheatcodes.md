# Nifi Dataflow templates

Apache NiFi provides users the ability to build very large and complex DataFlows using NiFi. 

This is achieved by using the basic components: Processor, Funnel, Input/Output Port, Process Group, and Remote Process Group. These can be thought of as the most basic building blocks for constructing a DataFlow. At times, though, using these small building blocks can become tedious if the same logic needs to be repeated several times. 

To solve this issue, NiFi provides the concept of a Template. A Template is a way of combining these basic building blocks into larger building blocks. Once a DataFlow has been created, parts of it can be formed into a Template. This Template can then be dragged onto the canvas, or can be exported as an XML file and shared with others. Templates received from others can then be imported into an instance of NiFi and dragged onto the canvas.


This [**Confluence space**](https://cwiki.apache.org/confluence/display/NIFI/Example+Dataflow+Templates) has few **Nifi templates** to help understand ans use Nifi flows for different usecases.

Author: Jennifer Barnabee

# Jython guide for Nifi 
### BOOK : [Python for the Java Platform](https://jython.readthedocs.io/en/latest/)
Authors:	Josh Juneau, Jim Baker, Victor Ng, Leo Soto, Frank Wierzbicki