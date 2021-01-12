# DiskDroid
DiskDroid is a new taint analysis tool, based on our disk-assisted IFDS.
# Publications
Scaling up the IFDS Algorithm with Efficient Disk-Assisted Computing In 18th Annual IEEE/ACM International Symposium on Code Generation and Optimization (CGO'21)
# Running The Command-Line Tool
You can evaluate our tools by following artifacts in our paper. Or you can run DiskDroid with default configuration by using the following command:

```
java -noverify -jar lib/s.jar \
    -a <APK File> \
    -p platforms \
    -s SourcesAndSinks.txt \
    -t EasyTaintWrapperSource.txt
```
