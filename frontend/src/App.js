import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components.Footer';
import Home from './components/Home';

function App() {
    return (
        <Router>
            <div>
                <Header />
                <Switch>
                    <Route path="/" exact component={Home} />
                </Switch>
                <Footer />
            </div>
        </Router>
    );
}

export default App;
