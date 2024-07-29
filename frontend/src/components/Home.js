import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Home() {
    const [message, setMessage] = useState('');

    useEffect(() => {
        axios.get('/api')
            .then(response => setMessage(response.data.Hello))
            .catch(error => console.error(error));
    }, []);

    return (
        <div>
            <h2>Home</h2>
            <p>{message}</p>
        </div>
    );
}

export default Home;
