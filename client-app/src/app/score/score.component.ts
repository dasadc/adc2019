import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';
import { CheckResults } from '../checkresults';
//import { QNumberList, ANumberList } from '../apiresponse';

@Component({
  selector: 'app-score',
  templateUrl: './score.component.html',
  styleUrls: ['./score.component.css']
})
export class ScoreComponent implements OnInit {
  score: Object;
  score_board: Object;
  score_board_num: number;
  score_board_header: string[];
  teams: string[];
  ok_point: Object;
  q_point: Object;
  bonus_point: Object;
  boardData: CheckResults;
  userList: string[];
  userInfo: Object[] = [];

  constructor(private adcService: AdcService) { }

  ngOnInit() {
    this.getScore();
    this.getUserList();
  }

  refreshScore() {
    this.getScore();
    this.getUserList();
  }

  createArray(data, teams) {
    let tbl = [];
    let rowLabel = Object.keys(data).sort();
    for (let r=0; r<rowLabel.length; r++) {
      let rowName = rowLabel[r];
      let row = [rowName];
      for (let c=0; c<teams.length; c++) {
        let team = teams[c];
        if (data[rowName][team] === void 0) {
          row.push('0');
        } else {
          row.push(''+data[rowName][team]);
        }
      } // loop c
      tbl.push(row.slice(0));
    } // loop r
    //console.log(tbl);
    return tbl;
  }

  createData() {
    //console.log(this.score);
    let s = this.score['score_board'];
    let h = s['/header/'];
    let n = (h === void 0) ? 0 : h.length;
    this.score_board = s;
    this.score_board_num = n;
    this.score_board_header = h;
    this.teams = Object.keys(this.score_board).slice(1)
    this.ok_point = this.createArray(this.score['ok_point'], this.teams);
    this.q_point = this.createArray(this.score['q_point'], this.teams);
    this.bonus_point = this.createArray(this.score['bonus_point'], this.teams);
  }

  getScore() {
    this.adcService.getScore()
      .subscribe(res => {
        //console.log('score getScore: res=', res);
        this.score = res;
        this.createData();
      });
  }

  getUserList() {
    this.userList = [];
    this.userInfo = [];
    this.adcService.getUserList()
      .subscribe(res => {
        //console.log('getUserList: res=', res);
        this.userList = res;
      	for (let i=0; i<this.userList.length; i++) {
      	  let userName = this.userList[i];
      	  this.adcService.getUserInfo(userName)
      	    .subscribe(res2 => {
      	      //console.log('getUserList: res2=', res2);
              if (res2['msg'] !== void 0) {
                let tmp = res2['msg'].split(':');
        	      this.userInfo.push({'username': tmp[0],
        				  'displayname': tmp[1],
        				  'uid': tmp[2],
        				  'gid': tmp[3]});
              }
      	    });
      	} // for i
      });
  }

  viewA(q: string, username: string, i: number, j: number) {
    let n = parseInt(q.slice(1), 10); // 'A01' --> '01' --> 1
    //console.log(q, n, username, i, j);
    this.adcService.getA(username, n)
      .subscribe(res => {
      	let aData: Object = res;
      	//console.log('A result=', aData['result']);
      	let aText: string = aData['result'][1]; // APIが汚い
      	//console.log(`A${n} =\n`, aText);
      	this.adcService.getQ(n)
      	  .subscribe(res => {
      	    let qText: string = res['text'];
                  //console.log(`Q${n} =\n`, qText);
      	    this.boardData = new CheckResults('info', qText, aText);
      	  })
      });
  }
}
