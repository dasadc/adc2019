import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'DAS2019 Algorithm Design Contest (ADC2019)';

  check() {
    console.log('Check now');
  }
}
