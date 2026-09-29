import React from 'react';
import { createRoot } from 'react-dom/client';
import { Amplify } from 'aws-amplify';
import App from './App.jsx';
import './styles.css';

const cfg = window.BEANTHERE_CONFIG || {};

if (cfg.userPoolId) {
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId: cfg.userPoolId,
        userPoolClientId: cfg.userPoolClientId,
        identityPoolId: cfg.identityPoolId,
        loginWith: { username: false, email: true },
      },
    },
  });
}

createRoot(document.getElementById('root')).render(<App config={cfg} />);
