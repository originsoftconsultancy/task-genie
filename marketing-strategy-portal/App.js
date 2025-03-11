import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import ContactUs from './contactUs'; // Adjust the path as necessary

const App = () => {
    return (
        <Router>
            <Switch>
                <Route path="/contact" component={ContactUs} />
                {/* Other routes can be added here */}
            </Switch>
        </Router>
    );
};

export default App; 