import json
t2={"x1":{"source":"sample","detector":"x1 detector"},"x2":{"source":"sample","detector":"x1 detector"},
"x3":{"source":"sample","detector":"x1 detector"}}
t1={"x1":{"source":"sample","detector":"x1 detector"}}
result={x:t2[x] for x in t2 if x not in t1}
print(json.dumps(result))
