import React, { useState } from 'react';
import styled from 'styled-components';
import { GoIssueOpened, GoIssueClosed, GoComment, GoSearch, GoTag, GoKebabHorizontal } from 'react-icons/go';
import { AiOutlineRobot, AiOutlineExclamationCircle } from 'react-icons/ai';

const Container = styled.div`
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const Title = styled.h1`
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #f0f6fc;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const NewIssueButton = styled.button`
  background-color: #238636;
  border: 1px solid #238636;
  border-radius: 6px;
  color: #fff;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  
  &:hover {
    background-color: #2ea043;
  }
`;

const FilterSection = styled.div`
  background-color: #161b22;
  border: 1px solid #30363d;
  border-radius: 6px 6px 0 0;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const FilterTabs = styled.div`
  display: flex;
  gap: 24px;
`;

const FilterTab = styled.button<{ active?: boolean }>`
  background: none;
  border: none;
  color: ${props => props.active ? '#f0f6fc' : '#7d8590'};
  font-size: 14px;
  cursor: pointer;
  padding: 8px 0;
  
  &:hover {
    color: #f0f6fc;
  }
`;

const SearchContainer = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`;

const SearchInput = styled.input`
  background-color: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #f0f6fc;
  padding: 6px 12px 6px 32px;
  width: 240px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #1f6feb;
  }
  
  &::placeholder {
    color: #7d8590;
  }
`;

const SearchIcon = styled(GoSearch)`
  position: absolute;
  left: 8px;
  color: #7d8590;
  font-size: 14px;
`;

const IssueList = styled.div`
  background-color: #0d1117;
  border: 1px solid #30363d;
  border-top: none;
  border-radius: 0 0 6px 6px;
`;

const IssueItem = styled.div`
  padding: 16px;
  border-bottom: 1px solid #21262d;
  cursor: pointer;
  
  &:hover {
    background-color: #161b22;
  }
  
  &:last-child {
    border-bottom: none;
  }
`;

const IssueHeader = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
`;

const IssueIcon = styled.div<{ status: 'open' | 'closed' }>`
  color: ${props => props.status === 'open' ? '#3fb950' : '#a855f7'};
  font-size: 16px;
  margin-top: 2px;
`;

const IssueContent = styled.div`
  flex: 1;
`;

const IssueTitle = styled.h3`
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #f0f6fc;
`;

const IssueMeta = styled.div`
  color: #7d8590;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
`;

const IssueLabels = styled.div`
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
`;

const Label = styled.span<{ color: string }>`
  background-color: ${props => props.color};
  color: #000;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
`;

const IssueActions = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CommentCount = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  color: #7d8590;
  font-size: 12px;
`;

const AIAnalyzedBadge = styled.div`
  background-color: #1f6feb;
  color: #fff;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const PriorityBadge = styled.div<{ priority: 'high' | 'medium' | 'low' }>`
  background-color: ${props => {
    switch (props.priority) {
      case 'high': return '#f85149';
      case 'medium': return '#fb8500';
      case 'low': return '#3fb950';
      default: return '#7d8590';
    }
  }};
  color: #fff;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 2px;
`;

const MoreButton = styled.button`
  background: none;
  border: none;
  color: #7d8590;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  
  &:hover {
    background-color: #30363d;
    color: #f0f6fc;
  }
`;

const Issues: React.FC = () => {
  const [activeTab, setActiveTab] = useState('open');

  const issues = [
    {
      id: 1,
      title: 'Add support for Python type hints in code analysis',
      status: 'open' as const,
      author: 'krishsanghvi',
      number: 15,
      comments: 2,
      aiAnalyzed: true,
      priority: 'high' as const,
      timeAgo: '1 hour ago',
      labels: [
        { name: 'enhancement', color: '#a2eeef' },
        { name: 'python', color: '#0075ca' }
      ]
    },
    {
      id: 2,
      title: 'False positive in security vulnerability detection',
      status: 'open' as const,
      author: 'user123',
      number: 14,
      comments: 5,
      aiAnalyzed: true,
      priority: 'medium' as const,
      timeAgo: '3 hours ago',
      labels: [
        { name: 'bug', color: '#d73a49' },
        { name: 'security', color: '#e99695' }
      ]
    },
    {
      id: 3,
      title: 'Improve performance of large file analysis',
      status: 'open' as const,
      author: 'developer456',
      number: 13,
      comments: 1,
      aiAnalyzed: false,
      priority: 'low' as const,
      timeAgo: '1 day ago',
      labels: [
        { name: 'performance', color: '#fbca04' }
      ]
    },
    {
      id: 4,
      title: 'Documentation for custom review rules',
      status: 'closed' as const,
      author: 'krishsanghvi',
      number: 12,
      comments: 3,
      aiAnalyzed: true,
      priority: 'medium' as const,
      timeAgo: '2 days ago',
      labels: [
        { name: 'documentation', color: '#0075ca' },
        { name: 'help wanted', color: '#008672' }
      ]
    }
  ];

  const filteredIssues = issues.filter(issue => {
    if (activeTab === 'open') return issue.status === 'open';
    if (activeTab === 'closed') return issue.status === 'closed';
    return true;
  });

  return (
    <Container>
      <Header>
        <Title>
          <GoIssueOpened />
          Issues
        </Title>
        <NewIssueButton>New issue</NewIssueButton>
      </Header>

      <FilterSection>
        <FilterTabs>
          <FilterTab 
            active={activeTab === 'open'} 
            onClick={() => setActiveTab('open')}
          >
            {issues.filter(issue => issue.status === 'open').length} Open
          </FilterTab>
          <FilterTab 
            active={activeTab === 'closed'} 
            onClick={() => setActiveTab('closed')}
          >
            {issues.filter(issue => issue.status === 'closed').length} Closed
          </FilterTab>
        </FilterTabs>
        
        <SearchContainer>
          <SearchIcon />
          <SearchInput placeholder="Search all issues" />
        </SearchContainer>
      </FilterSection>

      <IssueList>
        {filteredIssues.map((issue) => (
          <IssueItem key={issue.id}>
            <IssueHeader>
              <IssueIcon status={issue.status}>
                {issue.status === 'open' ? <GoIssueOpened /> : <GoIssueClosed />}
              </IssueIcon>
              
              <IssueContent>
                <IssueTitle>{issue.title}</IssueTitle>
                <IssueMeta>
                  <span>#{issue.number}</span>
                  <span>•</span>
                  <span>opened {issue.timeAgo} by {issue.author}</span>
                </IssueMeta>
                {issue.labels.length > 0 && (
                  <IssueLabels>
                    {issue.labels.map((label, index) => (
                      <Label key={index} color={label.color}>
                        <GoTag style={{ fontSize: '8px', marginRight: '2px' }} />
                        {label.name}
                      </Label>
                    ))}
                  </IssueLabels>
                )}
              </IssueContent>
              
              <IssueActions>
                <PriorityBadge priority={issue.priority}>
                  <AiOutlineExclamationCircle />
                  {issue.priority}
                </PriorityBadge>
                {issue.aiAnalyzed && (
                  <AIAnalyzedBadge>
                    <AiOutlineRobot />
                    AI Analyzed
                  </AIAnalyzedBadge>
                )}
                {issue.comments > 0 && (
                  <CommentCount>
                    <GoComment />
                    {issue.comments}
                  </CommentCount>
                )}
                <MoreButton>
                  <GoKebabHorizontal />
                </MoreButton>
              </IssueActions>
            </IssueHeader>
          </IssueItem>
        ))}
      </IssueList>
    </Container>
  );
};

export default Issues; 