import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { AiOutlineSearch, AiFillGithub } from 'react-icons/ai';
import { GoRepo, GoGitPullRequest, GoIssueOpened, GoPlus, GoBell } from 'react-icons/go';

const HeaderContainer = styled.header`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: #21262d;
  border-bottom: 1px solid #30363d;
  padding: 0 16px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const Logo = styled(Link)`
  display: flex;
  align-items: center;
  color: #f0f6fc;
  text-decoration: none;
  font-size: 24px;
  
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
  background-color: #010409;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #f0f6fc;
  padding: 8px 12px 8px 40px;
  width: 300px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #1f6feb;
    box-shadow: 0 0 0 3px rgba(31, 111, 235, 0.3);
  }
  
  &::placeholder {
    color: #7d8590;
  }
`;

const SearchIcon = styled(AiOutlineSearch)`
  position: absolute;
  left: 12px;
  color: #7d8590;
  font-size: 16px;
`;

const NavSection = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const RepoInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f0f6fc;
  font-size: 14px;
`;

const NavTabs = styled.nav`
  display: flex;
  align-items: center;
  gap: 24px;
`;

const NavLink = styled(Link)<{ active?: boolean }>`
  display: flex;
  align-items: center;
  gap: 8px;
  color: ${props => props.active ? '#f0f6fc' : '#7d8590'};
  text-decoration: none;
  font-size: 14px;
  padding: 20px 0;
  border-bottom: 2px solid ${props => props.active ? '#fd7e14' : 'transparent'};
  
  &:hover {
    color: #f0f6fc;
  }
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const IconButton = styled.button`
  background: none;
  border: none;
  color: #7d8590;
  font-size: 16px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  
  &:hover {
    color: #f0f6fc;
    background-color: #30363d;
  }
`;

const Avatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #30363d;
  border: 1px solid #21262d;
`;

const Header: React.FC = () => {
  const location = useLocation();

  return (
    <HeaderContainer>
      <LeftSection>
        <Logo to="/">
          <AiFillGithub />
        </Logo>
        
        <SearchContainer>
          <SearchIcon />
          <SearchInput placeholder="Search or jump to..." />
        </SearchContainer>
      </LeftSection>

      <NavSection>
        <RepoInfo>
          <GoRepo />
          <span>neural-code-reviewer</span>
        </RepoInfo>
        
        <NavTabs>
          <NavLink to="/" active={location.pathname === '/'}>
            <GoRepo />
            Code
          </NavLink>
          <NavLink to="/issues" active={location.pathname === '/issues'}>
            <GoIssueOpened />
            Issues
          </NavLink>
          <NavLink to="/pulls" active={location.pathname === '/pulls'}>
            <GoGitPullRequest />
            Pull requests
          </NavLink>
        </NavTabs>
      </NavSection>

      <RightSection>
        <IconButton>
          <GoPlus />
        </IconButton>
        <IconButton>
          <GoBell />
        </IconButton>
        <Avatar />
      </RightSection>
    </HeaderContainer>
  );
};

export default Header; 