//import logo from './logo.svg';

import './App.css';
import {BrowserRouter as Router, Routes, Route, Link, HashRouter} from "react-router-dom";
import Home from './components/Home';

function App() {
    return (
        <HashRouter basename = "/">
          <Routes>
            <Route path = "/" element={<Home />}/>
          </Routes>
        </HashRouter>
    );
  }

export default App;
