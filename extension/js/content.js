async function openBilingual () {
  // 开启双语字幕
  let tracks = document.getElementsByTagName('track')
  let en
  let zh
  if (tracks.length) {
    // 1. 遍历字幕节点，找到中英文字幕
    for (let i = 0; i < tracks.length; i++) {
      if (tracks[i].srclang === 'en') {
        en = tracks[i]
      } else if (tracks[i].srclang === 'zh-CN') {
        zh = tracks[i]
      } else if (tracks[i].srclang === 'zh-TW') {
        zh = tracks[i]
      }
    }
    // 2. 如果英文字幕存在，打开
    if (en) {
      en.track.mode = 'showing'
      // 3. 判定中文字幕是否存在, 如果存在，直接打开
      if (zh) {
        zh.track.mode = 'showing'
      } else {
        // 4. 如果不存在，开启翻译
        // Chrome 更新到 74 以后
        // 似乎首次设置 track.mode = 'showing' 到 cues 加载完毕之间有延迟？
        // 暂时先用 sleep 让 cues 有充足的时间加载字幕以确保正常工作，稍后再来解决
        await sleep(500)
        let cues = en.track.cues
        // 由于逐句翻译会大量请求翻译 API，需要减少请求次数
        let cuesText = ''
        for (let i = 0; i<cues.length; i++) {
          cues[i].text=cues[i].text.replace(/\s+/g,' ')
          if (cuesText) {
            cuesText += '\n\n' + cues[i].text
          }
          else{
            cuesText = cues[i].text
          }
        }
        getTranslation(cuesText, translatedText => {
          let translatedTextList=translatedText.split('\n\n')
          for (let i=0;i<cues.length;i++){
            console.log(translatedTextList[i])
            cues[i].text += '\n' + translatedTextList[i]
          } 
        })

      }
    }
  }
}

function sleep (ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

function getTranslation (words, callback) {
  // 通过谷歌翻译 API 进行翻译，输入待翻译的字符串，返回翻译完成的字符串
  const xhr = new XMLHttpRequest()
  let url = `https://127.0.0.1:5020/trans`
  xhr.open('POST', url, true)
  xhr.responseType = 'text'
  xhr.onload = function () {
    if (xhr.readyState === xhr.DONE) {
      if (xhr.status === 200 || xhr.status === 304) {
        console.log('正确返回')
        callback(xhr.responseText)
      }
    }
  }
  xhr.send(words)
}

// 设置监听，如果接收到请求，执行开启双语字幕函数
chrome.runtime.onMessage.addListener(
  function (request, sender) {
    openBilingual()
  }
)
