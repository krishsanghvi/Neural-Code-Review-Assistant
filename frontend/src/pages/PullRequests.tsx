import React, { useState } from 'react';
import styled from 'styled-components';
import { GoGitPullRequest, GoComment, GoCheck, GoX, GoSearch, GoKebabHorizontal } from 'react-icons/go';
import { AiOutlineRobot } from 'react-icons/ai';

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

const NewPRButton = styled.button`
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

const PRList = styled.div`
  background-color: #0d1117;
  border: 1px solid #30363d;
  border-top: none;
  border-radius: 0 0 6px 6px;
`;

const PRItem = styled.div`
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

const PRHeader = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
`;

const PRIcon = styled.div<{ status: 'open' | 'merged' | 'closed' }>`
  color: ${props => {
    switch (props.status) {
      case 'open': return '#3fb950';
      case 'merged': return '#a855f7';
      case 'closed': return '#f85149';
      default: return '#7d8590';
    }
  }};
  font-size: 16px;
  margin-top: 2px;
`;

const PRContent = styled.div`
  flex: 1;
`;

const PRTitle = styled.h3`
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #f0f6fc;
`;

const PRMeta = styled.div`
  color: #7d8590;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const PRActions = styled.div`
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

const AIReviewBadge = styled.div`
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

const PullRequests: React.FC = () => {
  const [activeTab, setActiveTab] = useState('open');

  const pullRequests = [
    {
      id: 1,
      title: 'Add enhanced security vulnerability detection',
      status: 'open' as const,
      author: 'krishsanghvi',
      number: 12,
      comments: 3,
      aiReviewed: true,
      timeAgo: '2 hours ago',
      branch: 'feature/security-detection'
    },
    {
      id: 2,
      title: 'Implement code quality suggestions engine',
      status: 'open' as const,
      author: 'krishsanghvi',
      number: 11,
      comments: 1,
      aiReviewed: true,
      timeAgo: '1 day ago',
      branch: 'feature/quality-engine'
    },
    {
      id: 3,
      title: 'Fix webhook signature verification',
      status: 'merged' as const,
      author: 'krishsanghvi',
      number: 10,
      comments: 2,
      aiReviewed: true,
      timeAgo: '2 days ago',
      branch: 'fix/webhook-signature'
    },
    {
      id: 4,
      title: 'Add comprehensive test coverage',
      status: 'closed' as const,
      author: 'krishsanghvi',
      number: 9,
      comments: 0,
      aiReviewed: false,
      timeAgo: '3 days ago',
      branch: 'feature/test-coverage'
    }
  ];

  const filteredPRs = pullRequests.filter(pr => {
    if (activeTab === 'open') return pr.status === 'open';
    if (activeTab === 'closed') return pr.status === 'closed' || pr.status === 'merged';
    return true;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open': return <GoGitPullRequest />;
      case 'merged': return <GoCheck />;
      case 'closed': return <GoX />;
      default: return <GoGitPullRequest />;
    }
  };

  return (
    <Container>
      <Header>
        <Title>
          <GoGitPullRequest />
          Pull requests
        </Title>
        <NewPRButton>New pull request</NewPRButton>
      </Header>

      <FilterSection>
        <FilterTabs>
          <FilterTab 
            active={activeTab === 'open'} 
            onClick={() => setActiveTab('open')}
          >
            {pullRequests.filter(pr => pr.status === 'open').length} Open
          </FilterTab>
          <FilterTab 
            active={activeTab === 'closed'} 
            onClick={() => setActiveTab('closed')}
          >
            {pullRequests.filter(pr => pr.status === 'closed' || pr.status === 'merged').length} Closed
          </FilterTab>
        </FilterTabs>
        
        <SearchContainer>
          <SearchIcon />
          <SearchInput placeholder="Search all pull requests" />
        </SearchContainer>
      </FilterSection>

      <PRList>
        {filteredPRs.map((pr) => (
          <PRItem key={pr.id}>
            <PRHeader>
              <PRIcon status={pr.status}>
                {getStatusIcon(pr.status)}
              </PRIcon>
              
              <PRContent>
                <PRTitle>{pr.title}</PRTitle>
                <PRMeta>
                  <span>#{pr.number}</span>
                  <span>•</span>
                  <span>opened {pr.timeAgo} by {pr.author}</span>
                  <span>•</span>
                  <span>{pr.branch}</span>
                </PRMeta>
              </PRContent>
              
              <PRActions>
                {pr.aiReviewed && (
                  <AIReviewBadge>
                    <AiOutlineRobot />
                    AI Reviewed
                  </AIReviewBadge>
                )}
                {pr.comments > 0 && (
                  <CommentCount>
                    <GoComment />
                    {pr.comments}
                  </CommentCount>
                )}
                <MoreButton>
                  <GoKebabHorizontal />
                </MoreButton>
              </PRActions>
            </PRHeader>
          </PRItem>
        ))}
      </PRList>
    </Container>
  );
};

export default PullRequests; 