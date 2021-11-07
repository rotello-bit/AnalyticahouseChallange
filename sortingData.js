function auotoSort() {
  const ss = SpreadsheetApp.getActiveSpreadsheet()
  const ws = ss.getSheetByName('Sayfa1')
  const range = ws.getRange(1,1,ws.getLastRow(),5)
  range.sort({column:5,ascending:false})
}

function onEdit(e) {
  const row = e.range.getRow()
  const column = e.range.getColumn()

  if(!(column === 5 && row >= 2)) return
  auotoSort()
}