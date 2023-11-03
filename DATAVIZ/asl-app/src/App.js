import logo from './logo.svg';
import './App.css';


//Inmporting the pages and components
import { ChakraProvider } from '@chakra-ui/react'
import Navbar from './components/navBar.js';
import Home from './pages/homePage.js';
import OurTeam from './pages/ourTeamPage.js';
import AboutOurModel from './pages/aboutOurModel.js';

function App() {
  return (
    <ChakraProvider>

    <div className="App">
      <Navbar />
      <Home />
      <OurTeam />
      <AboutOurModel />
    </div>

    </ChakraProvider>
  );
}

export default App;
