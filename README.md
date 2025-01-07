# SER001-SERCB斷面自動生成器

## v1.0.3

### Descriptions
1. 將RCAD的梁柱編號匯入ETABS **(v9)** 對應斷面併改名
1. Y向模型有將柱local轉向，且長寬對調
1. RCAD **(2019版本之後)** 的配筋亦輸出成SERCB用之 *.sect及.mat*

### Procedure Steps
1. ETABS建模完成，輸出e2k檔 (unit: ***kgf-cm***)
1. 將大梁配筋貼入e2k目錄下 *(Beam-Log.txt, tmp-Beam-Rebar.txt)*
1. 將柱配筋貼入e2k目錄下 *(Column-LOG.txt, tmp-Col-Rebar.txt\[標準型\])*
1. 執行程式後，可自動生成 *.sect及.mat*

>[!note]
> RCAD使用2019之後版本；ETABS使用v9.5版
>> 

### Update Notes
#### v1.0.3
1. RCAD版本更新到2019之後版本 (RCAD2016版本仍需用v1.0.2版使用)

#### v1.0.2
1. 忽略梁名或柱名找不到的情況