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

### To send all signals in a single json - Type A

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
## To send each signals to separate rows in database - Type B

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

## Aggregation 

### Type A (aggregating signals in a single json)

```
import json
from org.apache.commons.io import IOUtils
from java.nio.charset import StandardCharsets
from org.apache.nifi.processor.io import StreamCallback
from datetime import datetime

class PyStreamCallback(StreamCallback):
    def __init__(self, flowfile):
        self.ff = flowfile
        pass

    def process(self, inputStream, outputStream):
        algorithm = self.ff.getAttribute('algorithm')
        text = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
        inputList = json.loads(text)

        # Create dictionaries to accumulate values and timestamps for each signal
        signal_values = {}
        signal_time_from = {}
        signal_time_to = {}
        meta_info = {}  # Store meta information

        for inputDict in inputList:
            timestamp_str = inputDict['time']
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")

            # Store meta information (e.g., "opc_path" and "asset")
            meta_info['opc_path'] = inputDict.get('opc_path', '')
            meta_info['time'] = timestamp_str
            meta_info['asset'] = inputDict.get('asset', '')
            meta_info['algorithm'] = algorithm

            for signal_id, entry in json.loads(inputDict['value']).items():
                value = float(entry["value"])
                time = entry["time"]

                # Initialize lists and timestamps for each signal if not already created
                if signal_id not in signal_values:
                    signal_values[signal_id] = []
                    signal_time_from[signal_id] = timestamp
                    signal_time_to[signal_id] = timestamp
                else:
                    # Update timestamps
                    if timestamp < signal_time_from[signal_id]:
                        signal_time_from[signal_id] = timestamp
                    if timestamp > signal_time_to[signal_id]:
                        signal_time_to[signal_id] = timestamp

                # Append values to the respective signal's list
                signal_values[signal_id].append(value)

        # Create a dictionary to store aggregated results for each signal
        data_agg = {}

        for signal_id in signal_values:
            values = signal_values[signal_id]

            class OpcData(object):
                def __init__(self):
                    self.value = aggregate(values, algorithm)

            data_agg[signal_id] = OpcData().__dict__

        # Create the "value" dictionary to encapsulate the aggregated data, algorithm, time_from, and time_to
        value_data = {
            "data_agg": data_agg,
            "algorithm": meta_info['algorithm'],
            "time_from": min(signal_time_from.values()).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "time_to": max(signal_time_to.values()).strftime("%Y-%m-%d %H:%M:%S.%f")
        }

        # Create the final output object with rearranged fields
        final_output = {
            "time": meta_info['time'],
            "asset": meta_info['asset'],
            "opc_path": meta_info['opc_path'] + ";" + "agg=yes",
            "value": json.dumps(value_data)  # Serialize the "value_data" dictionary to JSON
        }

        data = json.dumps(final_output, indent=4)

        outputStream.write(bytearray(data.encode('utf-8')))

def average(data):
    return sum(data) / len(data)

def aggregate(data, algorithm):
    if algorithm == "average":
        return average(data)

flowFile = session.get()
if (flowFile != None):
    flowFile = session.write(flowFile, PyStreamCallback(flowFile))
    session.transfer(flowFile, REL_SUCCESS)
```

### Type B (aggregating signals in each row)
```
import json
from org.apache.commons.io import IOUtils
from java.nio.charset import StandardCharsets
from org.apache.nifi.processor.io import StreamCallback

def get_value(entry, value, dtype=float):
    return dtype(entry[value])

def average(data):
    return sum(data) / len(data)

def aggregate(data, algorithm):
    if algorithm == "average":
        return average(data)
    # Add more aggregation methods as needed

class PyStreamCallback(StreamCallback):
    def __init__(self, flowfile):
        self.ff = flowfile

    def process(self, inputStream, outputStream):
        algorithm = self.ff.getAttribute('algorithm')
        text = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
        inputList = json.loads(text)

        outputData = []
        signal_data = {}

        for innerList in inputList:
            for entry in innerList:
                opc_path = entry["opc_path"]
                time = entry["time"]
                value = get_value(entry, "value")
                asset = entry.get("asset", None)  # Get the "asset" field or set to None if not present

                if opc_path not in signal_data:
                    signal_data[opc_path] = {
                        "opc_path": opc_path,
                        "times": [],
                        "values": [],
                        "asset": asset  # Include the "asset" field in the signal_data dictionary
                    }

                signal_data[opc_path]["times"].append(time)
                signal_data[opc_path]["values"].append(value)

        for opc_path, data in signal_data.items():
            times = data["times"]
            values = data["values"]
            time_from = min(times)
            time_to = max(times)
            value = aggregate(values, algorithm)

            outputData.append({
                "opc_path": opc_path,
                "time_from": time_from,
                "time_to": time_to,
                "value": value,
                "algorithm": algorithm,
                "asset": data["asset"]  # Include the "asset" field in the output
            })

        data = json.dumps(outputData, indent=4)
        outputStream.write(bytearray(data.encode('utf-8')))

flowFile = session.get()
if (flowFile != None):
    flowFile = session.write(flowFile, PyStreamCallback(flowFile))
    session.transfer(flowFile, REL_SUCCESS)
```