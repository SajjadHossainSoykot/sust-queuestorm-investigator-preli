export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-left">
          <p className="footer-copy">
            Copyright © {currentYear} Team <span>!BlackBox</span>
          </p>

          <p className="footer-project">
            SUST QueueStorm Investigator
          </p>

          <p className="footer-team">
            <strong>Team Members:</strong> Julfikar Jim, Sajjad Hossain Soykot,
            Abu Ubaida
          </p>
        </div>

        <div className="footer-right">
          <p>
            <strong>API Developer:</strong>{' '}
            <a
              href="https://github.com/md-julfikar"
              target="_blank"
              rel="noreferrer"
            >
              @md-julfikar
            </a>
          </p>

          <p>
            <strong>Front End Developed by:</strong>{' '}
            <a
              href="https://github.com/SajjadHossainSoykot"
              target="_blank"
              rel="noreferrer"
            >
              @SajjadHossainSoykot
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}