import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'test-button-demo',
  template: `
    <input type="button" value="Submit" onclick="sendJSON()"/>
  `,
  styleUrls: ['./test-button-demo.component.scss'],
})
export class TestButtonDemoComponent implements OnInit {
  constructor() { }

  ngOnInit() {
  }

  sendJSON() {
    console.log("hello world");
    fetch('0.0.0.0:5000/api/bias', {
      method: 'post',
      body: JSON.stringify({})
    }).then(function(response) {
      return response.json();
    }).then(function(data) {
      // TODO: Viz
      console.log(data);
    });
  }

}
