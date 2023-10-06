# Nifi Dataflow templates

Apache NiFi provides users the ability to build very large and complex DataFlows using NiFi. 

This is achieved by using the basic components: Processor, Funnel, Input/Output Port, Process Group, and Remote Process Group. These can be thought of as the most basic building blocks for constructing a DataFlow. At times, though, using these small building blocks can become tedious if the same logic needs to be repeated several times. 

To solve this issue, NiFi provides the concept of a Template. A Template is a way of combining these basic building blocks into larger building blocks. Once a DataFlow has been created, parts of it can be formed into a Template. This Template can then be dragged onto the canvas, or can be exported as an XML file and shared with others. Templates received from others can then be imported into an instance of NiFi and dragged onto the canvas.


This [**Confluence space**](https://cwiki.apache.org/confluence/display/NIFI/Example+Dataflow+Templates) has few **Nifi templates** to help understand ans use Nifi flows for different usecases.

Author: Jennifer Barnabee

# Jython guide for Nifi 
### BOOK : [Python for the Java Platform](https://jython.readthedocs.io/en/latest/)
Authors:	Josh Juneau, Jim Baker, Victor Ng, Leo Soto, Frank Wierzbicki

## Nifi ExecuteScript python scripts

### To send all signals in a single json

UT501P

Output format: 
All signals in a single JSON
```
{
  "50240": {
    "time": 1695373739457,
    "value": "21.600000"
  },
  "50241": {
    "time": 1695373739457,
    "value": "26.400000"
  },
  "50242": {
    "time": 1695373739457,
    "value": "28.400000"
  },
  "50243": {
    "time": 1695373739457,
    "value": "1695373739"
  }
}
```
Corresponding script body,
```
import json
import java.io
import datetime

from org.apache.commons.io import IOUtils
from java.nio.charset import StandardCharsets
from org.apache.nifi.processor.io import StreamCallback

class PyStreamCallback(StreamCallback):
    def __init__(self, flowfile):
        self.ff = flowfile
        pass

    def process(self, inputStream, outputStream):
        text = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
        inputDict = json.loads(text)
        keys = list(inputDict.keys())

        outputdata = {}
        for a in range(1, len(keys)):
            outputdata[keys[a]] = inputDict[keys[a]]
		
        class OpcData(object):
            def __init__(self):
      	        self.time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                self.asset = "UT501P"
                self.opc_path = "ns=2;i=IDs"
                self.value = json.dumps(outputdata, indent=4)

        data = json.dumps(OpcData().__dict__, indent=4)
		
        outputStream.write(bytearray(data.encode('utf-8')))

flowFile = session.get()
if (flowFile != None):
    flowFile = session.write(flowFile,PyStreamCallback(flowFile))
    session.transfer(flowFile, REL_SUCCESS) 
    
```
## To send each signals to separate rows in database

UT501P
Output format: 
All signals in a separate values
```
21.6
26.4000
28.4
1695374614
```

Corresponding script body,
```
import json
import datetime

from org.apache.commons.io import IOUtils
from java.nio.charset import StandardCharsets
from org.apache.nifi.processor.io import StreamCallback

class PyStreamCallback(StreamCallback):
    def __init__(self, flowfile):
        self.ff = flowfile
        pass

    def process(self, inputStream, outputStream):
        text = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
        inputDict = json.loads(text)
        node_ids = ["50240", "50241", "50242", "50243"] #Edit this for different machines


        # Assuming inputDict has four node ids: "50240", "50241", "50242", and "50243"
        values = [float(inputDict[node_id]["value"]) for node_id in node_ids]

        # Write the values as separate rows with corresponding opc_path
        for node_id, value in zip(node_ids, values):
            row = {
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "asset": "UT501P",
                "opc_path": "ns=2;i=" + node_id,  # Corrected the syntax here
                "value": value
            }
            data = json.dumps(row, indent=4)
            outputStream.write(bytearray(data.encode('utf-8')) + b'\n')  # Add newline between rows

flowFile = session.get()
if (flowFile != None):
    flowFile = session.write(flowFile, PyStreamCallback(flowFile))
    session.transfer(flowFile, REL_SUCCESS)
```