import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import Header from './components/Header';
import RepositoryView from './pages/RepositoryView';
import PullRequests from './pages/PullRequests';
import Issues from './pages/Issues';
import './App.css';

const AppContainer = styled.div`
  min-height: 100vh;
  background-color: #0d1117;
  color: #f0f6fc;
`;

const MainContent = styled.main`
  padding-top: 64px; /* Account for fixed header */
`;

function App() {
  return (
    <AppContainer>
      <Router>
        <Header />
        <MainContent>
          <Routes>
            <Route path="/" element={<RepositoryView />} />
            <Route path="/pulls" element={<PullRequests />} />
            <Route path="/issues" element={<Issues />} />
          </Routes>
        </MainContent>
      </Router>
    </AppContainer>
  );
}

export default App;
