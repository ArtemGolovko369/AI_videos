// Рендер всего ролика в MP4: node tools/render.js out.mp4 [fps]
const { chromium } = require('playwright'); const fs=require('fs'), path=require('path'), {spawn}=require('child_process');
(async()=>{
  const out=process.argv[2]||'video.mp4', fps=+(process.argv[3]||25);
  const tl=JSON.parse(fs.readFileSync(path.resolve(__dirname,'timeline.json')));
  const audio=path.resolve(__dirname,'../audio/mix.wav');
  const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-i',audio,
    '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080}});
  p.on('pageerror',e=>console.error(String(e)));
  await p.goto('file://'+path.resolve(__dirname,'render.html'));
  await p.evaluate(tl=>window.init(tl),tl);
  const n=Math.ceil(tl.total*fps); const t0=Date.now();
  for(let i=0;i<n;i++){
    await p.evaluate(t=>frame(t),i/fps);
    const buf=await p.screenshot({type:'jpeg',quality:92});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    if(i%250===0) console.log(`${i}/${n} ${((Date.now()-t0)/1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done',out);
})();
