const fs=require('fs');const acorn=require('/opt/npm-tools/node_modules/acorn');const walk=require('/opt/npm-tools/node_modules/acorn-walk');
const html=fs.readFileSync(process.argv[2],'utf8');
const JP=/[぀-ヿ一-鿿]/;
const re=/<script(?![^>]*src)[^>]*>([\s\S]*?)<\/script>/g;let m,out=[],src;
function flat(n,parts){
  if(n.type==='BinaryExpression'&&n.operator==='+'){flat(n.left,parts);flat(n.right,parts);return}
  if(n.type==='Literal'&&typeof n.value==='string'){parts.push({s:n.value});return}
  if(n.type==='TemplateLiteral'){n.quasis.forEach((q,i)=>{parts.push({s:q.value.cooked});if(i<n.expressions.length)parts.push({h:src.slice(n.expressions[i].start,n.expressions[i].end)})});return}
  parts.push({h:src.slice(n.start,n.end)});
}
while((m=re.exec(html))){src=m[1];let ast;
  try{ast=acorn.parse(src,{ecmaVersion:'latest',sourceType:'script',allowReturnOutsideFunction:true})}catch(e){continue}
  walk.fullAncestor(ast,(n,anc)=>{
    const p=anc[anc.length-2];
    const isTop=!(p&&p.type==='BinaryExpression'&&p.operator==='+');
    if(!isTop)return;
    if(!((n.type==='BinaryExpression'&&n.operator==='+')||n.type==='TemplateLiteral'||(n.type==='Literal'&&typeof n.value==='string')))return;
    const parts=[];flat(n,parts);
    if(!parts.some(x=>x.s!==undefined&&JP.test(x.s)))return;
    let ctx='';for(let i=anc.length-2;i>=0;i--){const a=anc[i];if(a.type==='CallExpression'){ctx=src.slice(a.callee.start,a.callee.end).slice(0,40);break}}
    out.push({ctx,parts});
  });
}
fs.writeFileSync(process.argv[3],JSON.stringify(out));
console.error(out.length);
