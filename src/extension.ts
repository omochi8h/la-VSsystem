import { privateEncrypt } from 'crypto';
import * as vscode from 'vscode';
// eslint-disable-next-line @typescript-eslint/naming-convention
let dist_path = __dirname;
// eslint-disable-next-line @typescript-eslint/naming-convention
let project_path = dist_path.slice( 0, -4 );


//コンパイルエラーで動かない,SQlite3に繋げられない
// let sql_path = dist_path.slice( 0, -4 );
// const sqlite3 = require('sqlite3').verbose();
// const db = new sqlite3.Database(sql_path);
// console.log(db);

export function activate(context: vscode.ExtensionContext) {
	context.subscriptions.push(
		vscode.commands.registerCommand('assistsystem.assist', async () => {

			let activeEditor = vscode.window.activeTextEditor;
			let text :string = "";
			if (activeEditor){
			  text = activeEditor.document.getText();
			}
			vscode.window.showInformationMessage(`履歴送信しました`);

			//ソースコードのn-1行目を取得する
			let line1 = text.split(/\r\n|\r|\n/)[0];
			let line2 = text.split(/\r\n|\r|\n/)[1];
			let line3 = text.split(/\r\n|\r|\n/)[2];
			// 先頭から2文字を削除
			let number = line1.slice(2);
			let name = line2.slice(2);
			let task = line3.slice(2);

			// input.cに解答プログラムの書き込み.例のごとくC:\Users\stude\AppData\Local\Programs\Microsoft VS Codeに置かれてしまう．
			// @ts-ignore
			const removeHeads = (s, n) => s.split('\n').slice(n).join('\n');
			text = removeHeads(text, 3);
			const fs = require("fs");
			const program = text;
			// eslint-disable-next-line @typescript-eslint/naming-convention
			let task_path = project_path + 'task-program/input.c';
			// @ts-ignore
			fs.writeFile(task_path, program, (err) => {
			if (err) throw err;
				console.log('正常に書き込みが完了しました');
			});

			const date = new Date();
			const currentTime = formattedDateTime(date);
			//時間取得
			// @ts-ignore
			function formattedDateTime(date) {
			  const y = date.getFullYear();
			  const m = ('0' + (date.getMonth() + 1)).slice(-2);
			  const d = ('0' + date.getDate()).slice(-2);
			  const h = ('0' + date.getHours()).slice(-2);
			  const mi = ('0' + date.getMinutes()).slice(-2);
			  const s = ('0' + date.getSeconds()).slice(-2);
			  return y + m + d + h + mi + s;
			}

			const json = {
				"time": currentTime,
				"student_number": number,
				"student_name" : name,
				"task": task,
				"text": program
			};
			// eslint-disable-next-line @typescript-eslint/naming-convention
			const json_path = project_path + 'data.json';
			fs.writeFileSync(json_path, JSON.stringify(json));
			
			//jsonDataをPythonShell.runの第二引数にいれると直接jsonを送れる．
			// let jsonData = JSON.stringify(json);

			// @ts-ignore
			// eslint-disable-next-line @typescript-eslint/naming-convention
			const { PythonShell } = require('python-shell');
			// eslint-disable-next-line @typescript-eslint/naming-convention
			let py_path = project_path + 'assist-python/node_support.py';
			PythonShell.run(py_path, null, 
			// @ts-ignore
			(err, result) => {
				if (err) throw err;
					if (err) {
					console.log('finished');
					console.log(err);
				}
				console.log(result);
				
				if(result){
					console.log(result.length);
					vscode.window.showInformationMessage(`【Clear!】書き込み完了しました`);
				}
			});
		})
	);
	
	const button = vscode.window.createStatusBarItem(
		vscode.StatusBarAlignment.Right, 
		0
	);
	button.command = 'assistsystem.assist';
	button.text = 'コンパイル時に押してね！';
	context.subscriptions.push(button);
	button.show();

	var item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 10);
	let printDate = function () {
        var date = new Date();
        item.text = date.getHours().toString() + ":" + date.getMinutes().toString() + ":" + date.getSeconds().toString();
        item.show();
    };
    setInterval(printDate,100);
}