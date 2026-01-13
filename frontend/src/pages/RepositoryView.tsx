import React from 'react';
import styled from 'styled-components';
import { GoStar, GoRepoForked, GoEye, GoCode, GoHistory, GoDownload } from 'react-icons/go';
import { AiOutlineFile, AiOutlineFolder } from 'react-icons/ai';

const Container = styled.div`
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
`;

const RepoHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #30363d;
`;

const RepoInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const RepoTitle = styled.h1`
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #f0f6fc;
`;

const RepoDescription = styled.p`
  color: #7d8590;
  margin: 0;
  font-size: 16px;
`;

const RepoStats = styled.div`
  display: flex;
  gap: 16px;
  margin-top: 8px;
`;

const StatButton = styled.button`
  background: none;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #f0f6fc;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  
  &:hover {
    background-color: #30363d;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 8px;
`;

const Button = styled.button`
  background-color: #21262d;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #f0f6fc;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    background-color: #30363d;
  }
  
  &.primary {
    background-color: #238636;
    border-color: #238636;
    
    &:hover {
      background-color: #2ea043;
    }
  }
`;

const FileExplorer = styled.div`
  background-color: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  margin-bottom: 24px;
`;

const FileExplorerHeader = styled.div`
  background-color: #161b22;
  padding: 12px 16px;
  border-bottom: 1px solid #30363d;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 6px 6px 0 0;
`;

const BranchInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7d8590;
  font-size: 14px;
`;

const CommitInfo = styled.div`
  color: #7d8590;
  font-size: 14px;
`;

const FileList = styled.div`
  
`;

const FileItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-bottom: 1px solid #21262d;
  cursor: pointer;
  
  &:hover {
    background-color: #21262d;
  }
  
  &:last-child {
    border-bottom: none;
  }
`;

const FileIcon = styled.div`
  color: #7d8590;
  font-size: 16px;
`;

const FileName = styled.span`
  color: #58a6ff;
  font-size: 14px;
  flex: 1;
`;

const FileMessage = styled.span`
  color: #7d8590;
  font-size: 12px;
  flex: 2;
`;

const FileTime = styled.span`
  color: #7d8590;
  font-size: 12px;
`;

const ReadmeSection = styled.div`
  background-color: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 24px;
`;

const ReadmeHeader = styled.h2`
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #f0f6fc;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ReadmeContent = styled.div`
  color: #e6edf3;
  line-height: 1.6;
  
  p {
    margin: 0 0 16px 0;
  }
  
  h1, h2, h3 {
    color: #f0f6fc;
    margin: 24px 0 16px 0;
  }
`;

const RepositoryView: React.FC = () => {
  const files = [
    { name: 'neural-code-reviewer', type: 'folder', message: 'Initial project structure', time: '2 hours ago' },
    { name: '.gitignore', type: 'file', message: 'Add gitignore', time: '2 hours ago' },
    { name: 'README.md', type: 'file', message: 'Add project documentation', time: '2 hours ago' },
    { name: 'requirements.txt', type: 'file', message: 'Add Python dependencies', time: '2 hours ago' },
  ];

  return (
    <Container>
      <RepoHeader>
        <RepoInfo>
          <RepoTitle>neural-code-reviewer</RepoTitle>
          <RepoDescription>
            An AI-powered GitHub Action/bot that automatically reviews code commits, detects security vulnerabilities, and suggests improvements.
          </RepoDescription>
          <RepoStats>
            <StatButton>
              <GoStar />
              Star
            </StatButton>
            <StatButton>
              <GoRepoForked />
              Fork
            </StatButton>
            <StatButton>
              <GoEye />
              Watch
            </StatButton>
          </RepoStats>
        </RepoInfo>
        
        <ActionButtons>
          <Button>
            <GoCode />
            Code
          </Button>
          <Button className="primary">
            <GoDownload />
            Download
          </Button>
        </ActionButtons>
      </RepoHeader>

      <FileExplorer>
        <FileExplorerHeader>
          <BranchInfo>
            <span>main</span>
            <span>•</span>
            <span>4 commits</span>
          </BranchInfo>
          <CommitInfo>
            <GoHistory />
            Latest commit 2 hours ago
          </CommitInfo>
        </FileExplorerHeader>
        
        <FileList>
          {files.map((file, index) => (
            <FileItem key={index}>
              <FileIcon>
                {file.type === 'folder' ? <AiOutlineFolder /> : <AiOutlineFile />}
              </FileIcon>
              <FileName>{file.name}</FileName>
              <FileMessage>{file.message}</FileMessage>
              <FileTime>{file.time}</FileTime>
            </FileItem>
          ))}
        </FileList>
      </FileExplorer>

      <ReadmeSection>
        <ReadmeHeader>
          <AiOutlineFile />
          README.md
        </ReadmeHeader>
        <ReadmeContent>
          <h1>Neural Code Review Assistant</h1>
          <p>
            An AI-powered GitHub Action/bot that automatically reviews code commits, 
            detects security vulnerabilities, suggests improvements, and learns from 
            codebase patterns to provide increasingly personalized feedback.
          </p>
          
          <h2>Features</h2>
          <p>
            • Automated code review on pull requests<br/>
            • Security vulnerability detection<br/>
            • Code quality suggestions<br/>
            • Learning from codebase patterns<br/>
            • Integration with GitHub webhooks
          </p>
          
          <h2>Getting Started</h2>
          <p>
            This project uses FastAPI for the backend service that handles GitHub webhooks 
            and performs AI-powered code analysis.
          </p>
        </ReadmeContent>
      </ReadmeSection>
    </Container>
  );
};

export default RepositoryView; 