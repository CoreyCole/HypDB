import { Component } from '@angular/core';

@Component({
  selector: 'hyp-root',
  template: `
    <!--The content below is only a placeholder and can be replaced.-->
    <mat-toolbar color="primary">HypDB</mat-toolbar>
    <router-outlet></router-outlet>
  `,
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'hyp';
}
