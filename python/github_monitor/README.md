# soulGuard.py
用于搜索github上相关内容,目前只是简单的搜索并存储到本地文件，需要更多的功能可以修改，比如存储到数据库等，然后通过钉钉报警，可以监控公司代码是否有在github上泄漏。

### 使用
```shell
soulGuard.py <print|file path> "search keyword"
```

### 搜索结果
```json
 python3 ch8/soulGuard.py   print  "fonzie1006"    
打印结果
{
  "create_time":"2020-01-04 16:29:42",
  "data":[
    {
      "file_name":"README.md",
      "html_url":"https://github.com/fonzie1006/shortlink/blob/15454fef32d3e77dff049c0ed42171cf0d12034c/README.md",
      "keyword":"fonzie1006",
      "repo_name":"shortlink",
      "repo_url":"https://github.com/fonzie1006/shortlink",
      "sha":"a6a946bd4e1c2eb0a43187a8301f4febe1f9dfcc",
      "user_avatar":"https://avatars2.githubusercontent.com/u/31980550?v=4",
      "user_name":"fonzie1006",
      "user_url":"https://github.com/fonzie1006"
    },
    {
      "file_name":"redis.go",
      "html_url":"https://github.com/fonzie1006/shortlink/blob/22e4052e011731bdae5a4162f0d930bbea645f78/pkg/gredis/redis.go",
      "keyword":"fonzie1006",
      "repo_name":"shortlink",
      "repo_url":"https://github.com/fonzie1006/shortlink",
      "sha":"769f3f6e8608cb5fab7f3cf5f38a324a41f2aac5",
      "user_avatar":"https://avatars2.githubusercontent.com/u/31980550?v=4",
      "user_name":"fonzie1006",
      "user_url":"https://github.com/fonzie1006"
    },
    {
      "file_name":"router.go",
      "html_url":"https://github.com/fonzie1006/shortlink/blob/96662898f8bab869428e27b2edeff3167c7c1f67/routers/router.go",
      "keyword":"fonzie1006",
      "repo_name":"shortlink",
      "repo_url":"https://github.com/fonzie1006/shortlink",
      "sha":"740db8e891826eeab61bbf0b4137d9770188c7d2",
      "user_avatar":"https://avatars2.githubusercontent.com/u/31980550?v=4",
      "user_name":"fonzie1006",
      "user_url":"https://github.com/fonzie1006"
    },
    {
      "file_name":"shortlink.go",
      "html_url":"https://github.com/fonzie1006/shortlink/blob/96662898f8bab869428e27b2edeff3167c7c1f67/routers/api/v1/shortlink.go",
      "keyword":"fonzie1006",
      "repo_name":"shortlink",
      "repo_url":"https://github.com/fonzie1006/shortlink",
      "sha":"c70007127101c60a8c115e655611a5a101f73b06",
      "user_avatar":"https://avatars2.githubusercontent.com/u/31980550?v=4",
      "user_name":"fonzie1006",
      "user_url":"https://github.com/fonzie1006"
    },
    {
      "file_name":"response.go",
      "html_url":"https://github.com/fonzie1006/shortlink/blob/96662898f8bab869428e27b2edeff3167c7c1f67/pkg/app/response.go",
      "keyword":"fonzie1006",
      "repo_name":"shortlink",
      "repo_url":"https://github.com/fonzie1006/shortlink",
      "sha":"141fcb5bc6b081d4da05e75bdbdff53bc81e2cd4",
      "user_avatar":"https://avatars2.githubusercontent.com/u/31980550?v=4",
      "user_name":"fonzie1006",
      "user_url":"https://github.com/fonzie1006"
    },
........
........
........
........
........
........
........
........
........
........
  ],
  "modify_time":"2020-01-04 16:29:42",
  "total":11
}

```


### 推荐相关应用
* [github monitor](https://github.com/VKSRC/Github-Monitor)
