(rough around the edges, haven't touched Python in months) 

This script gets all devices from Connectwise Automate and checks their CPU against `cpu_support.csv`. A new CSV titled `windows_11_compatibility.csv` will be output once done.

Required environmental variables:
- `CONNECTWISE_ACCESS_TOKEN`
- `CONNECTWISE_CLIENT_ID`

Resources:
- [ConnectWise Client ID](https://developer.connectwise.com/ClientID)
- [ConnectWise Access Token](https://developer.connectwise.com/Products/ConnectWise_Automate/Integrating_with_Automate/API/Developer_Guide)
- [Windows 11 Supported Intel Processors](https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-supported-intel-processors)
- [Windows 11 Supported AMD Processors](https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-supported-amd-processors)
- [Windows 11 Supported Qualcomm Processors](https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-supported-qualcomm-processors)