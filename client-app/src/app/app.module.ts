import { BrowserModule }      from '@angular/platform-browser';
import { NgModule }           from '@angular/core';
import { FormsModule }        from '@angular/forms';
import { HttpClientModule }   from '@angular/common/http';

import { AppRoutingModule }   from './app-routing.module';
import { AppComponent }       from './app.component';
import { FileComponent }      from './file/file.component';
import { FileComponent2 }     from './file/file2.component';

import { NgxFileDropModule }  from 'ngx-file-drop';
import { FileViewComponent }  from './file-view/file-view.component';
import { FileViewComponent2 } from './file-view/file-view2.component';
import { FileCheckerComponent } from './file-checker/file-checker.component';
import { ResultViewComponent } from './result-view/result-view.component';

@NgModule({
  declarations: [
    AppComponent,
    FileComponent,
    FileComponent2,
    FileViewComponent,
    FileViewComponent2,
    FileCheckerComponent,
    ResultViewComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule,
    NgxFileDropModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
