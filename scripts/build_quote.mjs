import fs from 'node:fs/promises';
import {Workbook, SpreadsheetFile} from '../.tools/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const model=JSON.parse(await fs.readFile('deliverables/cost-model.json','utf8'));
const wb=Workbook.create();
const quote=wb.worksheets.add('BaoGia');
const calc=wb.worksheets.add('TinhGia');
const drivers=wb.worksheets.add('Sizing');
const heads=['Component','Ý nghĩa','Ghi chú','Chi phí/tháng (USD)','Bằng chứng'];
quote.getRange('A1:E1').values=[heads];
const rows=model.rows;
quote.getRange(`A2:E${rows.length+1}`).values=rows;
calc.getRange('A1:F1').values=[['Hạng mục','Công thức / giả định','USD/tháng','Nguồn','Ngày kiểm tra','Trạng thái']];
calc.getRange(`A2:F${rows.length+1}`).values=rows.map(r=>[r[1],r[2],r[3],r[4],model.as_of,'Planning rate: cần capture SKU trước nộp']);
// Cost rows link to the calculation schedule; estimate assumptions are editable there.
for(let i=0;i<rows.length;i++) quote.getRange(`D${i+2}`).formulas=[[`=TinhGia!C${i+2}`]];
let end=rows.length+2;
quote.getRange(`A${end}:E${end}`).values=[['TOTAL','Production + staging + vận hành + dự phòng','USD/tháng, chưa VAT; H6/H8/restore chưa đo',null,'']];
quote.getRange(`D${end}`).formulas=[[`=SUM(D2:D${end-1})`]];
const entries=[['Giả định / kết quả','Giá trị','Đơn vị / giải thích'],...Object.entries(model.inputs).map(([k,v])=>[k,v,'Input']),...model.tasks.map(t=>[t.level,t.requests,`${t.share*100}% tasks; ${t.input}/${t.output} cumulative in/out tokens; ${t.model}`]),...Object.entries(model.summary).filter(([k,v])=>typeof v==='number').map(([k,v])=>[k,v,'Từ script deterministic; thay input JSON và rebuild để cập nhật']),['Lưu ý','H6/H8/DR chưa kiểm thử','Giá tham chiếu, không phải hóa đơn AWS. Không trừ ưu đãi.'],['Phạm vi','us-east-1; US geo inference','Không có slide deck hoặc application implementation trong gói thiết kế này.']];
drivers.getRange(`A1:C${entries.length}`).values=entries;
for(const s of [quote,calc,drivers]){
 s.showGridLines=false;
 s.getUsedRange().format.font={name:'Arial',size:11};
 s.getUsedRange().format.verticalAlignment='top';
 s.getUsedRange().format.wrapText=true;
 s.getUsedRange().format.rowHeight=s===drivers?38:s===calc?76:58;
 const width=s===drivers?'A1:C1':s===quote?'A1:E1':'A1:F1';
 s.getRange(width).format={fill:'#14384C',font:{name:'Arial',bold:true,color:'#FFFFFF',size:11},rowHeight:32};
 s.freezePanes.freezeRows(1);
 s.getRange('A:A').format.columnWidth=s===drivers?34:23;
 s.getRange('B:B').format.columnWidth=s===drivers?24:s===calc?78:40;
 s.getRange('C:C').format.columnWidth=s===calc?18:78;
 if(s!==drivers){s.getRange('D:D').format.columnWidth=s===quote?23:54;s.getRange('E:E').format.columnWidth=s===quote?56:18;}
 if(s===calc)s.getRange('F:F').format.columnWidth=40;
}
quote.tabColor='#14384C';calc.tabColor='#3E7187';
quote.getRange(`D2:D${end}`).setNumberFormat('#,##0.00');
calc.getRange(`C2:C${rows.length+1}`).setNumberFormat('#,##0.00');
calc.getRange(`C2:C${rows.length+1}`).format.font.color='#2456A6';
quote.getRange(`A${end}:E${end}`).format.fill='#E4EDF0';quote.getRange(`A${end}:E${end}`).format.font.bold=true;
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:`BaoGia!A${end}:E${end}`,include:'values,formulas',maxChars:1000})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!',options:{useRegex:true,maxResults:20},maxChars:600})).ndjson);
for(const name of ['BaoGia','TinhGia','Sizing']){
 const p=await wb.render({sheetName:name,range:name==='Sizing'?'A1:C8':name==='BaoGia'?'A1:D6':'A1:C6',scale:1,format:'png'});
 await fs.writeFile(`deliverables/${name}-preview.png`,new Uint8Array(await p.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save('deliverables/Eviaura_baogia.xlsx');
