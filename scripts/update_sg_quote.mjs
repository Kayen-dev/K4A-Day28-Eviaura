import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile,FileBlob} from '../.tools/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const m=JSON.parse(await fs.readFile('deliverables/cost-model.json','utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load('deliverables/archive/us-east-1/Eviaura_baogia.xlsx'));
const quote=wb.worksheets.getItem('BaoGia'),calc=wb.worksheets.getItem('TinhGia'),sizing=wb.worksheets.getItem('Sizing');
if(m.rows.length!==27)throw Error('Preserve 27-line quote structure');
quote.getRange('A2:E28').values=m.rows;
calc.getRange('A2:F28').values=m.rows.map((r,i)=>[r[1],r[2],null,r[4],m.as_of,m.row_skus[i].length?'AWS public SKU checked: '+m.row_skus[i].join(', '):'Assumption / monthly allowance']);
calc.getRange('C2:C28').formulas=m.formulas.map(f=>[f]);
for(let i=0;i<27;i++)quote.getRange(`D${i+2}`).formulas=[[`=TinhGia!C${i+2}`]];
quote.getRange('D29').formulas=[['=ROUND(SUM(D2:D28),2)']];
quote.getRange('C29').values=[['ap-southeast-1 primary; model inference has APAC/Global/Oregon exceptions; USD/month, before VAT']];
const old=sizing.getUsedRange().values;
const inputEntries=Object.entries(m.inputs),numericEntries=Object.entries(m.summary).filter(([k,v])=>typeof v==='number');
const entries=[['Giả định / kết quả','Giá trị','Đơn vị / giải thích'],...inputEntries.map(([k,v])=>[k,v,'Input giữ nguyên workload, cập nhật rate Singapore']),...m.tasks.map(t=>[t.level,t.requests,`${t.share*100}% tasks; ${t.input}/${t.output} cumulative input/output; ${t.model}`]),...numericEntries.map(([k,v])=>[k,v,'Snapshot từ cost-model.json, rebuild script để cập nhật']),['Lưu ý','H6/H8/DR chưa kiểm thử','SKU prices checked 16/10/2026. Workload, labor and allowance are estimates.'],['Phạm vi','ap-southeast-1 primary',m.inference_scope]];
sizing.getUsedRange().clear({applyTo:'contents'});
sizing.getRange(`A1:C${entries.length}`).values=entries;
// Extend the existing style only to the newly affected comparison rows.
sizing.getRange(`A2:C${entries.length}`).format.font={name:'Arial',size:11};
sizing.getRange(`A2:C${entries.length}`).format.wrapText=true;
sizing.getRange(`A2:C${entries.length}`).format.rowHeight=42;
quote.getRange('A2:E28').format.rowHeight=92;
calc.getRange('A2:F28').format.rowHeight=100;
quote.getRange('A29:E29').format.rowHeight=70;
sizing.getRange(`A${entries.length}:C${entries.length}`).format.rowHeight=85;
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'BaoGia!A29:E29',include:'values,formulas',maxChars:800})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!',options:{useRegex:true,maxResults:20},maxChars:500})).ndjson);
for(const name of ['BaoGia','TinhGia','Sizing']){
 const preview=await wb.render({sheetName:name,range:name==='Sizing'?`A${entries.length-3}:C${entries.length}`:name==='BaoGia'?'A4:E8':'A4:F8',scale:1,format:'png'});
 await fs.writeFile(`deliverables/${name}-preview.png`,new Uint8Array(await preview.arrayBuffer()));
}
const xlsx=await SpreadsheetFile.exportXlsx(wb);
await xlsx.save('deliverables/G03_baogia.xlsx');
// Preserve the earlier user-facing file link, with identical updated bytes.
await fs.copyFile('deliverables/G03_baogia.xlsx','deliverables/Eviaura_baogia.xlsx');
