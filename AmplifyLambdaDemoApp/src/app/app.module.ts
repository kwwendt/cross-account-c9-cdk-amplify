import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { Amplify } from 'aws-amplify';
import { AmplifyAuthenticatorModule } from '@aws-amplify/ui-angular';

import { AppComponent } from './app.component';
import awsmobile from '../aws-exports';

Amplify.configure(awsmobile);

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    AmplifyAuthenticatorModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }