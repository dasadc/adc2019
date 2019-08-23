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
import { BoardViewComponent } from './board-view/board-view.component';
import { LoginComponent } from './login/login.component';
import { MyAccountComponent } from './my-account/my-account.component';
import { StatusBarComponent } from './status-bar/status-bar.component';
import { UploadQComponent } from './upload-q/upload-q.component';
import { ContestComponent } from './contest/contest.component';
import { ScoreComponent } from './score/score.component';
import { AdminComponent } from './admin/admin.component';

@NgModule({
  declarations: [
    AppComponent,
    FileComponent,
    FileComponent2,
    FileViewComponent,
    FileViewComponent2,
    FileCheckerComponent,
    ResultViewComponent,
    BoardViewComponent,
    LoginComponent,
    MyAccountComponent,
    StatusBarComponent,
    UploadQComponent,
    ContestComponent,
    ScoreComponent,
    AdminComponent
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
