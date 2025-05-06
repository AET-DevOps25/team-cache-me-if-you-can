import Navigator from '../../nav/Navigator';
import { useState } from 'react';

export default function Home() {
    const [submit, setSubmit] = useState(false);

    return (
        <Navigator />
    );
}