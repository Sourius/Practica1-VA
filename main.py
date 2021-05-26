import argparse
from Detector import Detector

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Trains and executes a given detector over a set of testing images')
    parser.add_argument(
        '--detector', type=str, nargs="?", default="MSER_TS_Detector", help='Detector string name')
    parser.add_argument(
        '--train_path', default="train", help='Select the training data dir')
    parser.add_argument(
        '--test_path', default="test", help='Select the testing data dir')

    args = parser.parse_args()

    detector = Detector()
    print("Entrenando...")
    detector.train_from_dir(args.train_path)
    print("Procesando imagenes...")
    detector.detect_from_dir(args.test_path)
    print("Imagenes procesadas.")

    # Evaluate sign detections
