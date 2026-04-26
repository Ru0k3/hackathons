import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="page not-found-page">
      <h1>404</h1>
      <p>This page doesn&apos;t exist.</p>
      <Link to="/wardrobe" className="btn-primary">Go to wardrobe</Link>
    </div>
  );
}
