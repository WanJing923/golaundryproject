// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBTIjB4Zz60jlnjVRNBeLEc8YDOVjsErRU",
  authDomain: "golaundry-906c7.firebaseapp.com",
  databaseURL: "https://golaundry-906c7-default-rtdb.firebaseio.com",
  projectId: "golaundry-906c7",
  storageBucket: "golaundry-906c7.appspot.com",
  messagingSenderId: "63734818081",
  appId: "1:63734818081:web:24fa422edc2802ac47ca60",
  measurementId: "G-2000030N7P"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);