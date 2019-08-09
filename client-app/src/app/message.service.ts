import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  text: string = undefined;

  add(message: string) {
    this.text = message;
    console.log('message', this.text);
  }
  clear() {
    this.text = undefined;
  }
}
